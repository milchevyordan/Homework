import { TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AppComponent } from './app.component';

const API = 'http://127.0.0.1:8000/api/user';

describe('AppComponent', () => {
    let httpMock: HttpTestingController;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            declarations: [AppComponent],
            imports: [FormsModule],
            providers: [provideHttpClient(), provideHttpClientTesting()],
        }).compileComponents();
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => httpMock.verify());

    function setup(username: string) {
        const fixture = TestBed.createComponent(AppComponent);
        fixture.componentInstance.githubUsername = username;
        fixture.componentInstance.search();
        return fixture;
    }

    it('renders followers, repos and technologies', async () => {
        const fixture = setup('octocat');
        httpMock.expectOne(`${API}?username=octocat`).flush({
            username: 'octocat', name: 'The Octocat', avatar_url: null, profile_url: null,
            followers: 42, repo_count: 2, most_used_language: 'Ruby',
            repos: [
                { name: 'hello', language: 'Ruby', url: '#', description: null, stars: 1, fork: false },
                { name: 'site', language: null, url: '#', description: null, stars: 0, fork: false },
            ],
            languages: [{ name: 'Ruby', count: 1 }],
            messages: {},
        });
        await fixture.whenStable();
        const text = (fixture.nativeElement as HTMLElement).textContent!;
        expect(text).toContain('42');
        expect(text).toContain('Ruby (1)');
        expect(text).toContain('hello');
        expect(text).toContain('No language detected');
    });

    it('shows empty-state messages', async () => {
        const fixture = setup('empty');
        httpMock.expectOne(`${API}?username=empty`).flush({
            username: 'empty', name: null, avatar_url: null, profile_url: null,
            followers: 0, repo_count: 0, most_used_language: null, repos: [], languages: [],
            messages: {
                followers: 'empty does not have any followers yet.',
                repos: 'empty does not have any public repositories.',
            },
        });
        await fixture.whenStable();
        const text = (fixture.nativeElement as HTMLElement).textContent!;
        expect(text).toContain('does not have any followers yet');
        expect(text).toContain('does not have any public repositories');
    });

    it('shows the backend error for a missing user', async () => {
        const fixture = setup('nobody');
        httpMock.expectOne(`${API}?username=nobody`).flush(
            { detail: "GitHub user 'nobody' does not exist." },
            { status: 404, statusText: 'Not Found' },
        );
        await fixture.whenStable();
        expect(fixture.nativeElement.querySelector('.error').textContent).toContain('does not exist');
    });

    it('asks for a username when the input is empty', async () => {
        const fixture = setup('   ');
        await fixture.whenStable();
        expect(fixture.nativeElement.querySelector('.error').textContent).toContain('Please enter');
    });
});
